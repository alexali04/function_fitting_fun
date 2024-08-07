import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Callable, Any
from torch.utils.data import DataLoader
import numpy as np
import logging

from func_learning.utils.plotting_utils import (
    plot_labels_and_predictions
)


def train_model(
    model: nn.Module, 
    criterion: Callable,  
    n_epochs: int, 
    train_loader: DataLoader, 
    val_loader: DataLoader, 
    function_description: str,
    func_to_learn: Callable,
    folder: str,
    domain_start: int,
    domain_end: int,
    plot_range: List[int],
    plot: bool=True
) -> None:
    """
    print_epoch_mod: prints training, validation loss every print_epoch_mod epochs \n
    available loss functions: 'mse', 'cross_entropy' \n
    returns validation predictions for each epoch    
    """

    loss_func = criterion()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)

    for epoch in range(n_epochs):

        training_loss = 0.0
        val_loss = 0.0
        
        # Training model
        model.train()
        for X, y in train_loader:
            y_pred = model(X)                       # Generate predictions
            loss = loss_func(y_pred, y)             # Compute Loss
            optimizer.zero_grad()                   # Zero out influence of previously computed gradients
            loss.backward()                         # Compute gradients for all tensors in neural network
            optimizer.step()                        # Update parameters according to gradient (and external factors like LR, momentum)

            training_loss += loss.item()            # Aggregating batch loss  

        model.eval()                                    # Disables train-only features (i.e. dropout)
        if plot:    
            X_plot_vals = np.linspace(domain_start, domain_end, 5000)
            y_plot_vals = func_to_learn(X_plot_vals)
            y_pred_vals = model(torch.tensor(X_plot_vals, dtype=torch.float32).unsqueeze(1)).detach().numpy().flatten()

            plot_labels_and_predictions(
                inputs=X_plot_vals,
                labels=y_plot_vals,
                predictions=y_pred_vals,
                folder=folder,
                id=f"train_epoch_{epoch}",
                function_description=function_description,
                epoch=epoch,
                show_image=False,
                sample_limit=4000,
                save_fig=True,
                static_range=True,
                y_low=plot_range[0],
                y_high=plot_range[1],
            )

        # Validating model
        with torch.no_grad():                           # Turn off gradient computations
            for X_val, y_val in val_loader:
                y_val_pred = model(X_val)                      
                loss = loss_func(y_val_pred, y_val)
                val_loss += loss.item()

            if epoch % 100 == 0:
                print(f"{epoch} Batch Training Loss: {training_loss / len(train_loader)}")
                print(f"{epoch} Batch Validation Loss: {val_loss / len(val_loader)}")


def evaluate_model_on_test_set(
    model: nn.Module, 
    X_test: np.ndarray, 
    y_test: np.ndarray, 
    loss_func: Callable, 
    loss_func_description: str, 
    func_description: str, 
    folder: str,
    plot: bool = False
) -> Any:
    """
    Evaluates model on test dataset using loss_func

    Args:
        model: trained model to evaluate
        X_test: test features to evaluate on
        y_test: test labels
        loss_func: loss function to use
        loss_func_description: description of loss function i.e. "Cross Entropy Loss"
        func_description: description of function to be approximated
        folder: path of folder to write plot to
        plot: if True, plot y_test against predictions. else, just return loss
    
    Returns:
        output of loss function


    """
    X_test = torch.tensor(X_test, dtype=torch.float32).unsqueeze(1)
    y_test = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)
    loss_func = loss_func()

    model.eval()
    y_preds = model(X_test)
    loss = loss_func(y_preds, y_test)
    logging.info(f"{loss_func_description}: Test Loss {loss}")

    if plot: 
        plot_labels_and_predictions(
            inputs=X_test.detach().numpy(),
            labels=y_test.detach().numpy(), 
            predictions=y_preds.detach().numpy(), 
            folder=folder, 
            id="results", 
            function_description=func_description, 
            epoch=-1,
            show_image=False,      
            sample_limit=6000,
            save_fig=True
        )

    return loss




            




            